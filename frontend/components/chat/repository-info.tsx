'use client';

import { useEffect, useState, useMemo } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Star, GitFork, Calendar, Code2, FolderOpen, FileCode } from 'lucide-react';
import { useAppStore } from '@/lib/store';

// Helper function to parse tree structure from backend
function parseTreeStructure(treeString: string) {
  const lines = treeString.split('\n').filter(line => line.trim());
  const items: Array<{ name: string; type: 'folder' | 'file'; indent: number }> = [];
  
  for (const line of lines) {
    // Skip header lines
    if (line.includes('Directory structure:') || line.trim() === '') continue;
    
    // Count indentation level
    const indent = line.search(/[└├│]/);
    if (indent === -1) continue;
    
    // Extract name (remove tree characters and whitespace)
    const name = line.replace(/[└├│─\s]/g, '').replace(/\//g, '').trim();
    if (!name) continue;
    
    // Determine if folder or file
    const isFolder = line.includes('/') || line.includes('├') || line.includes('└');
    
    items.push({
      name,
      type: isFolder ? 'folder' : 'file',
      indent: Math.floor(indent / 4),
    });
  }
  
  return items.slice(0, 20); // Limit to first 20 items for display
}

export function RepositoryInfo() {
  const { repository, isLoading } = useAppStore();
  
  // Parse the real tree from backend
  const fileTree = useMemo(() => {
    if (!repository?.tree) return [];
    return parseTreeStructure(repository.tree);
  }, [repository?.tree]);
  
  // Extract summary info
  const summaryInfo = useMemo(() => {
    if (!repository?.summary) {
      return {
        filesCount: 0,
        tokens: '0',
        description: '',
      };
    }
    
    const summary = repository.summary;
    const filesMatch = summary.match(/Files analyzed: (\d+)/);
    const tokensMatch = summary.match(/Estimated tokens: ([\d.]+k?)/);
    
    return {
      filesCount: filesMatch ? parseInt(filesMatch[1]) : 0,
      tokens: tokensMatch ? tokensMatch[1] : '0',
      description: `Analyzed ${filesMatch ? filesMatch[1] : 0} files`,
    };
  }, [repository?.summary]);

  if (!repository) return null;

  return (
    <ScrollArea className="h-[calc(100vh-8rem)]">
      <div className="space-y-4 pr-4">
        {/* Repository Info */}
        <Card className="p-4 bg-card">
          <div className="space-y-3">
            <div>
              <h3 className="font-semibold text-lg mb-1">{repository.name}</h3>
              <p className="text-xs text-muted-foreground">by {repository.owner}</p>
            </div>

            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            ) : (
              <>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {summaryInfo.description}
                </p>

                <div className="flex flex-wrap gap-2 pt-2">
                  <Badge variant="secondary" className="gap-1">
                    <FileCode className="h-3 w-3" />
                    {summaryInfo.filesCount} files
                  </Badge>
                  <Badge variant="secondary" className="gap-1">
                    <Code2 className="h-3 w-3" />
                    {summaryInfo.tokens} tokens
                  </Badge>
                </div>

                {repository?.summary && (
                  <div className="text-xs text-muted-foreground pt-2 font-mono bg-muted/30 p-2 rounded">
                    {repository.summary.split('\n').slice(0, 3).join('\n')}
                  </div>
                )}
              </>
            )}
          </div>
        </Card>

        {/* File Structure */}
        {!isLoading && fileTree.length > 0 && (
          <Card className="p-4 bg-card">
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <FolderOpen className="h-4 w-4" />
              Repository Structure
            </h4>
            <div className="space-y-1 text-sm font-mono">
              {fileTree.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 py-1 px-2 rounded hover:bg-muted/50 cursor-pointer"
                  style={{ paddingLeft: `${item.indent * 16 + 8}px` }}
                >
                  {item.type === 'folder' ? (
                    <>
                      <FolderOpen className="h-3.5 w-3.5 text-primary flex-shrink-0" />
                      <span className="text-foreground truncate">{item.name}</span>
                    </>
                  ) : (
                    <>
                      <FileCode className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                      <span className="text-muted-foreground truncate">{item.name}</span>
                    </>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Processing Indicator */}
        {isLoading && (
          <Card className="p-4 bg-card">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                <span className="text-sm font-medium">Processing repository...</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Analyzing code structure, issues, and discussions
              </p>
            </div>
          </Card>
        )}
      </div>
    </ScrollArea>
  );
}

